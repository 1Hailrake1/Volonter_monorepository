from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text, Boolean, UniqueConstraint, \
    CheckConstraint, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    '''базовый класс наследник для orm моделей'''
    pass


'''
Пользователи
'''
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    fullname = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    avatar_url = Column(String(500), nullable=True)
    date_birth = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True, index=True)
    date_created = Column(DateTime, server_default=func.now(), nullable=False)
    date_last_login = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

'''
Навыки
'''
class Skills(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

'''
Навыки пользователя связь многие ко многим
'''
class UserSkills(Base):
    __tablename__ = 'user_skills'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'skill_id', name='uq_user_skills'),
    )

'''
Информация о ролях    
    # системные:
        admin - администратор
        user - пользователь
    # пользовательские:
        волонтёр
        организатор
'''
class RolesInfo(Base):
    __tablename__ = 'roles_info'
    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

'''
Сами роли как связи между RolesInfo и Users
'''
class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles_info.id', ondelete='RESTRICT'), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

'''
События - мероприятия созданные организатором
    status
     # pending approved - подверждается админом
     # canceled - отменяется организатором
     # passed - автоматически выставляется системой в случае если now.date > end_data и status != canceled|pending
'''
class Events(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    organizer_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False, index=True)
    required_volunteers = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending', index=True)
    event_image_url = Column(String(500), nullable=True)
    date_created = Column(DateTime, server_default=func.now())

'''
Теги id и название
'''
class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

'''
Теги событий, связь многие ко многим
'''
class EventTags(Base):
    __tablename__ = 'event_tags'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('event_id', 'tag_id', name='uq_event_tag_event'),
    )

'''
Необходимые навыки для участия в евенте
Связана 1 ко многим event_id 1:n 
'''
class RequiredEventsSkills(Base):
    __tablename__ = 'required_events_skills'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('event_id', 'skill_id', name='uq_event_required_event'),
    )

'''
Заявки на участие в событии, волонтёр подаёт
 status
 # pending aproved rejected
 Можно подать без сопроводительного сообщения message - nullable
 volunteer_id - user_id, с ролью волонтёра
'''
class Applications(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    volunteer_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    message = Column(Text, nullable=True)
    status = Column(String(20), default='pending', index=True)
    date_created = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('event_id', 'volunteer_id', name='uq_event_volunteer'),
    )
'''
Обратная связь после проведения мероприятия 
from_user_id - может быть как волонтёром, так и организатором, то есть любая сущность user_id с ЛЮБОЙ! ролью
to_user_id - может быть любой сущностью которая принадлежит множеству user_id участвующих в мероприятии event_id.
Можно дать ревью пользователю не из пользователей которые участвовали в event, например простому пользователю или админу
Нельзя дать ревью НА пользователя который не участвовал в евенте!
'''
class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    from_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    to_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = Column(Integer, nullable=False) # 1 - 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
'''
Уведомления
Посылаются в случае:
1) тех работ
2) мероприятий как напоминание организатору и участнику
3) получения обратной связи 
4) любых других непреднамеренных случаях
'''
class Notifications(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
